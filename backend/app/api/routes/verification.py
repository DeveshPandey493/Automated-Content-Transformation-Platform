from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.output import GeneratedOutput
from app.db.models.verification import VerificationReport, ExtractedClaim
from app.core.exceptions import OutputNotFoundError
from app.schemas.verification import VerificationReportResponse
from app.services.verification.service import VerificationService

router = APIRouter(prefix="/verification", tags=["Factual Verification"])

@router.post("/{output_id}", response_model=VerificationReportResponse, status_code=status.HTTP_200_OK)
def run_verification(
    output_id: str,
    db: Session = Depends(get_db)
):
    output = db.get(GeneratedOutput, output_id)
    if not output:
        raise OutputNotFoundError(output_id)

    report = VerificationService.verify_output(output_id, db)
    return report

@router.get("/{output_id}", response_model=VerificationReportResponse)
def get_verification_report(
    output_id: str,
    db: Session = Depends(get_db)
):
    output = db.get(GeneratedOutput, output_id)
    if not output:
        raise OutputNotFoundError(output_id)

    report = output.verification_report
    if not report:
        # Run on-demand if not existing
        report = VerificationService.verify_output(output_id, db)

    return report
