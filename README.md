## システムの用途
ACM等の学会のプロシーディングスを各研究１ページの紹介スライドにまとめるコードです



## セットアップ

### 0. プロシーディングスのダウンロード
まずはACM DL等からプロシーディングスをダウンロードします。

ダウンロード元は  
CHIだと https://dl.acm.org/conference/chi/proceedings  
IUIだと https://dl.acm.org/conference/iui/proceedings  
UISTだと https://dl.acm.org/conference/uist/proceedings  
等に過去のプロシーディングス一覧がまとまっています。

他のACMの多くの学会も以下のように学会のacronymをパスを設定すると出てきます。
https://dl.acm.org/conference/****/proceedings

続いて、以降のセットアップを用いてセットアップをしてください。

### 1. Python仮想環境の作成
Pythonの仮想環境を作成し、`requirements.txt`をインストールします。

```bash
python -m venv env
source env/bin/activate  # Windowsの場合は `env\Scripts\activate`
pip install -r requirements.txt
```

### 2. OpenAI APIキーの設定
OpenAIのAPIキーを環境変数`OPENAI_API_KEY`として設定します。

```bash
export OPENAI_API_KEY="your_openai_api_key"  # Windowsの場合は `set OPENAI_API_KEY=your_openai_api_key`
```

### 3. スクリプトの実行
以下の順にスクリプトを実行します。

```bash
# 3.1 parse.pyの実行
python parse.py <pdf file name>

# 3.2 keyvisual.pyの実行
python keyvisual.py

```

### 4. データベースの作成
`create_db.py`を実行して論文データベースを作成します。

```bash
python create_db.py
```

OpenAIの出力の揺らぎやJSONのパースの問題でデータベースの作成時にエラーが出る場合があります。
標準出力と、summarize/error/　にエラーが書き出されるようになっています。

```
Error in inserting data: Incorrect number of bindings supplied. 
```
というエラーが（新規に）ある場合にはcreate_db.pyを再実行してください。

すでに要約済みのものはスキップした上で、正常に完了していない研究についての要約をデータベースに追加します。

### 5. 論文要約PDFの作成
`make_pdf_jp.py`もしくは`make_pdf_en.py`を実行して、論文の要約PDFを作成します。

```bash
python make_pdf_jp.py  # 日本語の要約PDFを作成する場合。日本語版はoutputディレクトリに、全論文を要約したPDFと（デフォルトでは）100ページ毎に分割したPDF群が出力されます。
python make_pdf_en.py  # 英語の要約PDFを作成する場合
```
## 参考
このスクリプトは以下の議論支援システムの実装の一部分を活用して実装したものです。LLMの活用や情報収集支援、議論支援などにご関心がある方はよければご覧下さい。　　

Serendipity Wall: A Discussion Support System Using Real-time Speech Recognition and Large Language Model  
Serendipity Wall: 会話文字起こしのベクター検索と大規模言語モデルによる議論支援システム  
https://dl.acm.org/doi/10.1145/3652920.3652931

```
@inproceedings{10.1145/3652920.3652931,
author = {Imamura, Shota and Hiraki, Hirotaka and Rekimoto, Jun},
title = {Serendipity Wall: A Discussion Support System Using Real-time Speech Recognition and Large Language Model},
year = {2024},
isbn = {9798400709807},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3652920.3652931},
doi = {10.1145/3652920.3652931},
abstract = {Group discussions are important for exploring new ideas. Discussion support systems will enhance human creative ability through better discussion experiences. One method to support discussions is presenting relevant keywords or images. However, the context of the conversation and information tended not to be taken into account. Therefore, we propose a system that develops group discussions by presenting related information in response to discussions. As a specific example, this study addressed academic discussions among HCI researchers. During brainstorming sessions, the system continuously transcribes the dialogue and generates embedding vectors of the discussions. These vectors are matched against those of existing research articles to identify relevant studies. Then, the system presented relevant studies on the screen with summaries by an LLM. In case studies, this system had the effect of broadening the topics of discussion and facilitating the acquisition of new knowledge. This study showed the possibility that AI can facilitate discussion by providing discussion support through information retrieval and summarizing.},
booktitle = {Proceedings of the Augmented Humans International Conference 2024},
pages = {237–247},
numpages = {11},
keywords = {Discussion, Embedding Vectors, Facilitation, Information retrieval, Large Language Models},
location = {<conf-loc>, <city>Melbourne</city>, <state>VIC</state>, <country>Australia</country>, </conf-loc>},
series = {AHs '24}
}
```
