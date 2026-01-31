import flet as ft
import fitz  # PyMuPDF
import os

#FONT_PATH = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"

def replace_text(input_pdf, output_pdf, src, dst):
    doc = fitz.open(input_pdf)

    '''
    if not os.path.exists(FONT_PATH):
        print(f"Error: {FONT_PATH} が見つかりません。")
        return
    '''

    for page in doc:
        # 1. 置換対象の場所をすべて探す
        rects = page.search_for(src)
        if not rects:
            continue

        # 2. まず「墨消し注釈」を付ける（文字はまだ入れない）
        #for r in rects:
        #    page.add_redact_annot(r)
        # y0 (矩形の上端の座標) が最小のものを1つだけ取得
        top_rect = min(rects, key=lambda r: r.y0)
        page.add_redact_annot(top_rect)

        # 3. 墨消しを実行（これで元の文字データが物理的に消え、白抜きになります）
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

        # 4. 白くなった場所に、改めてフォントを指定して文字を書き込む
        #for r in rects:
        # insert_text の座標 (r.x0, r.y1) は「左下」基準です。
        # 少しだけ上にずらす（r.y1 - 2など）と、元の位置に綺麗に収まりやすいです。
        page.insert_text(
            (top_rect.x0, top_rect.y1 - 1),
            dst,
            fontname="japan",
            fontsize=top_rect.height* 0.9,  # 枠より少し小さくすると自然です
            color=(0, 0, 0)  # 黒色
        )

    doc.save(output_pdf)
    doc.close()

def main(page: ft.Page):
    page.title = "PDF 日本語文字列置換ツール"
    page.window_width = 600
    page.window_height = 420

    picked_file = ft.Text("PDF未選択")

    src_text = "請求書" #ft.TextField(label="置換前（3文字漢字）")
    dst1_text = ft.TextField(value="見積書",label="置換文字列1")
    dst2_text = ft.TextField(value="納品書",label="置換文字列2")

    def pick_pdf(e: ft.FilePickerResultEvent):
        if e.files:
            picked_file.value = e.files[0].path
            page.update()

    file_picker = ft.FilePicker(on_result=pick_pdf)
    page.overlay.append(file_picker)

    def run_replace(e):
        if not picked_file.value or not os.path.exists(picked_file.value):
            return

        base, ext = os.path.splitext(picked_file.value)

        replace_text(
            picked_file.value,
            base + "Q.pdf",
            src_text,
            dst1_text.value,
        )

        replace_text(
            picked_file.value,
            base + "D.pdf",
            src_text,
            dst2_text.value,
        )

        page.snack_bar = ft.SnackBar(
            ft.Text("PDF1 / PDF2 を生成しました")
        )
        page.snack_bar.open = True
        page.update()

    page.add(
        ft.Column(
            [
                ft.ElevatedButton(
                    "PDFを選択",
                    on_click=lambda _: file_picker.pick_files(
                        allow_multiple=False,
                        file_type=ft.FilePickerFileType.CUSTOM,
                        allowed_extensions=["pdf"],
                    ),
                ),
                picked_file,
                #src_text,
                ft.Text(value="「請求書」を書き換えます"),
                dst1_text,
                dst2_text,
                ft.ElevatedButton("生成", on_click=run_replace),
            ],
            spacing=15,
        )
    )

ft.app(target=main)
