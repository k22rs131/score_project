import os
from io import BytesIO
from PIL import Image
from image_processing import process_and_convert

def test_process_and_convert(input_path):
    """
    指定画像を処理してPDF化し、結果を保存・確認するテスト関数
    """
    if not os.path.exists(input_path):
        print(f"❌ ファイルが見つかりません: {input_path}")
        return

    print("🔍 入力画像:", input_path)

    # 処理実行
    result_pdf, paper_type = process_and_convert(input_path)

    # 出力ファイル名を生成
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_pdf_path = f"output_{base_name}_{paper_type}.pdf"

    # PDF保存
    with open(output_pdf_path, "wb") as f:
        f.write(result_pdf.read())

    print(f"✅ 出力完了: {output_pdf_path}")
    print(f"📄 判定結果: {paper_type}")

if __name__ == "__main__":
    # テストしたい画像ファイルパスを指定（例: test_images/sample.jpg）
    test_image_path = "test_images/机（不純物なし）.jpg"

    # 出力ディレクトリ作成
    os.makedirs("test_images", exist_ok=True)

    # まだ画像がない場合の案内
    if not os.path.exists(test_image_path):
        print(f"⚠️ テスト画像がありません。'{test_image_path}' に配置してください。")
    else:
        test_process_and_convert(test_image_path)
