import csv
file_path = "enavi202607(4177).csv"

with open(file_path, "r", encoding="utf-8-sig", newline="") as csv_file:
    #newline=""は、CSVを読み書きするときの改行処理をPython側で勝手に変えないための指定。
    #utf-8-sigは、CSV先頭に付いている余計な目印も自動で取り除いてくれる。
    reader = csv.reader(csv_file)
# for val in f:→ ファイルを普通の文章として1行ずつ読む.splitが必要だが単純にsplit(",")すると、店名とかまで途中で分割されてしまう。
# for row in csv.reader(f):→ CSVとして1行ずつ読み、列にも分ける
    for index, row in enumerate(reader):#全部の行を読むなら、enumerate()はいらない。行番号が欲しいときだけ使うもの。
        print(row)

        # 最初の5行だけ表示
        if index >= 4:
            break