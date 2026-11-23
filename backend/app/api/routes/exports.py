import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.output import GeneratedOutput
from app.core.exceptions import OutputNotFoundError
from app.services.export.exporter import export_output

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("/{output_id}")
def export_output_endpoint(
    output_id: str,
    format: str = Query("pdf", description="Export format: pdf, docx, md, txt"),
    include_verification: bool = Query(True, description="Include verification report"),
    include_evaluation: bool = Query(True, description="Include evaluation metrics"),
    db: Session = Depends(get_db),
):
    """Export a generated output in the requested format."""
    output = db.get(GeneratedOutput, output_id)
    if not output:
        raise OutputNotFoundError(output_id)

    try:
        content, filename, media_type = export_output(
            output=output,
            format_type=format,
            include_verification=include_verification,
            include_evaluation=include_evaluation,
        )
    except ValueError as e:
        return PlainTextResponse(
            content=str(e),
            status_code=400,
        )

    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )