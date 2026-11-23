"""
Router para exportação de dados (Excel).
"""
import io
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import NotaFiscal, EmpresaGrupo
from config import ANO_CORRENTE
from services.vencimento import NOMES_MESES_ABREV

router = APIRouter(prefix="/api/exportacao", tags=["Exportação"])


@router.get("/excel")
def exportar_excel(
    mes: int = None,
    ano: int = None,
    db: Session = Depends(get_db),
):
    """Exporta notas fiscais para Excel no formato familiar."""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        return {"error": "openpyxl não instalado. Execute: pip install openpyxl"}

    if not ano:
        ano = ANO_CORRENTE

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    meses = [mes] if mes else range(1, 13)

    for m in meses:
        nome_aba = f"{NOMES_MESES_ABREV.get(m, str(m))}-{str(ano)[2:]}"
        ws = wb.create_sheet(title=nome_aba)

        # Estilos
        header_font = Font(bold=True, size=12, color="FFFFFF")
        header_fill = PatternFill(start_color="6366F1", end_color="6366F1", fill_type="solid")
        ok_fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
        pend_fill = PatternFill(start_color="F59E0B", end_color="F59E0B", fill_type="solid")
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        # Título
        ws.merge_cells('A1:G1')
        ws['A1'] = f"CONTROLE DE NOTAS FISCAIS - {NOMES_MESES_ABREV.get(m)}/{ano}"
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = Alignment(horizontal='center')

        # Headers
        headers = ["EMPRESA", "Nº DA NOTA", "Nº DO PEDIDO", "VALOR", "GRUPO EMALTO", "VENCIMENTO", "PRÉ-NOTA"]
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=2, column=col, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
            cell.border = thin_border

        # Dados
        notas = db.query(NotaFiscal).options(
            joinedload(NotaFiscal.empresa_grupo)
        ).filter(
            NotaFiscal.mes_referencia == m,
            NotaFiscal.ano_referencia == ano,
        ).order_by(NotaFiscal.empresa_fornecedor).all()

        for row_idx, nf in enumerate(notas, 3):
            ws.cell(row=row_idx, column=1, value=nf.empresa_fornecedor).border = thin_border
            ws.cell(row=row_idx, column=2, value=nf.numero_nota).border = thin_border
            ws.cell(row=row_idx, column=3, value=nf.numero_pedido).border = thin_border
            valor_cell = ws.cell(row=row_idx, column=4, value=nf.valor)
            valor_cell.number_format = '#,##0.00'
            valor_cell.border = thin_border
            ws.cell(row=row_idx, column=5, value=nf.empresa_grupo.sigla if nf.empresa_grupo else "").border = thin_border
            ws.cell(row=row_idx, column=6, value=nf.data_vencimento.strftime("%d/%m/%Y") if nf.data_vencimento else "").border = thin_border
            status_cell = ws.cell(row=row_idx, column=7, value=nf.status_pre_nota)
            status_cell.border = thin_border
            status_cell.alignment = Alignment(horizontal='center')
            if nf.status_pre_nota == "OK":
                status_cell.fill = ok_fill
                status_cell.font = Font(color="FFFFFF", bold=True)
            else:
                status_cell.fill = pend_fill

        # Ajustar larguras
        widths = [25, 18, 15, 15, 20, 15, 12]
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    # Salvar em memória
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = f"Controle_NFs_{ano}.xlsx"
    if mes:
        filename = f"Controle_NFs_{NOMES_MESES_ABREV.get(mes)}_{ano}.xlsx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
