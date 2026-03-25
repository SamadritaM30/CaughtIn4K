from flask import Blueprint, current_app, flash, render_template, request, redirect, url_for
from flask_login import login_required

from models import HumanReview
from extensions import db

review_bp = Blueprint("review", __name__)


@review_bp.route("/review")
@login_required
def review_page():
    items = HumanReview.query.filter_by(reviewed=False).order_by(HumanReview.id.desc()).all()
    reviewed_items = HumanReview.query.filter_by(reviewed=True).order_by(HumanReview.id.desc()).limit(20).all()
    return render_template("review.html", items=items, reviewed_items=reviewed_items)


@review_bp.route("/submit_review/<int:review_id>", methods=["POST"])
@login_required
def submit_review(review_id):
    item = HumanReview.query.get_or_404(review_id)

    is_correct = request.form.get("is_correct")
    correct_label = request.form.get("correct_label", "").strip().upper()

    if is_correct == "yes":
        item.is_correct = True
        item.human_label = item.predicted_label
        item.reviewed = True
        db.session.commit()
        flash(f"Review #{review_id} marked as correct.", "success")

    elif is_correct == "no":
        if not correct_label:
            flash("Please provide the correct label before submitting.", "error")
            return redirect(url_for("review.review_page"))

        item.is_correct = False
        item.human_label = correct_label
        item.reviewed = True
        db.session.commit()

        # --- Trigger incremental retraining ---
        _trigger_retrain(item, correct_label)

    else:
        flash("Invalid submission.", "error")

    return redirect(url_for("review.review_page"))


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _trigger_retrain(item, correct_label):
    """Fire incremental retraining for one corrected image."""
    try:
        from retrain import retrain_on_correction

        base_output_dir = current_app.config.get("MODEL_OUTPUT_DIR", "")
        dataset_root    = current_app.config.get("DATASET_ROOT", "")
        item_name       = getattr(item, "item_name", None) or _infer_item_name(item.img_path)

        if not dataset_root:
            flash(
                "Correction saved, but DATASET_ROOT is not configured — "
                "skipping automatic retraining. Set DATASET_ROOT in app.py.",
                "warning",
            )
            return

        if not item_name:
            flash(
                "Correction saved, but item name could not be determined — "
                "skipping automatic retraining.",
                "warning",
            )
            return

        result = retrain_on_correction(
            img_path        = item.img_path,
            correct_label   = correct_label,
            predicted_label = item.predicted_label,
            item_name       = item_name,
            base_output_dir = base_output_dir,
            dataset_root    = dataset_root,
        )

        if result["success"]:
            flash(
                f"Model retrained with your correction! "
                f"Weights updated at: {result['model_path']}",
                "retrain",
            )
        else:
            flash(f"Correction saved but retraining failed: {result['message']}", "warning")

    except Exception as exc:
        flash(f"Correction saved but retraining raised an error: {exc}", "warning")


def _infer_item_name(img_path):
    """
    Heuristic: img_path stored by run_model.py looks like
    'results/{defect_category}_{filename}.png'.
    Extract the first segment before the first underscore.
    """
    import os
    basename = os.path.basename(img_path)
    parts = basename.split("_")
    if parts:
        return parts[0].lower()
    return None
