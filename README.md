# haproxy-ingress-controller-docs-scraping

## build & run

仮想環境の作成

```
python -m venv .venv
```

仮想環境の有効化

```
source .venv/bin/activate
```

依存関係ライブラリのインストール

```
pip install -r  requirements.txt
```

## スクレイピングの実行

### https://www.haproxy.com/documentation/kubernetes-ingress/ ページのスクレイプ実行

overviewページのスクレイプ実行

```
mkdir csv
cp  jrnote.yml jrnote.yml.bak
cp  jrnote.haproxy-ingress.overview.yml jrnote.yml
python jrnote/jrnote.py > csv/haproxy-ingress-controller-docs-ovewview.csv
```

communityのスクレイプ実行

```
cp  jrnote.haproxy-ingress.community.yml jrnote.yml
python jrnote/jrnote.py > csv/haproxy-ingress-controller-docs-community.csv
```

enterpriseのスクレイプ実行

```
cp  jrnote.haproxy-ingress.enterprise.yml jrnote.yml
python jrnote/jrnote.py > csv/haproxy-ingress-controller-docs-enterprise.csv
```

adminのスクレイプ実行

```
cp jrnote.haproxy-ingress.admin.yml jrnote.yml
python jrnote/jrnote.py > csv/haproxy-ingress-controller-docs-admin.csv
```

ingress tutorialsのスクレイプ実行

```
cp jrnote.haproxy-ingress.ingressTutorials.yml jrnote.yml
python jrnote/jrnote.py > csv/haproxy-ingress-controller-docs-ingress-tutorials.csv
```

gatewayApi tutorialsのスクレイプ実行

```
cp jrnote.haproxy-ingress.gatewayApi.tutorials.yml jrnote.yml
python jrnote/jrnote.py > csv/haproxy-ingress-controller-docs-gatewayapi-tutorials.csv
```

