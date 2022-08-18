# skripsi

# how to run
1. download https://github.com/fathanq/web-crawler/
2. import skripsi.sql
3. install dependencies (python -m pip install -r requirements.txt)
4. change max_allowed_packet inside my.ini on section [mysqld] according to your data size (modified_crawling.py sekali run (default setting) bisa menghasilkan sekitar 150MB-an dictionary)
5. run modified_crawling.py
6. run onehotencode.py (memindahkan data dari data yang di crawl modified crawl (dbcrawl) ke database skripsi, lalu membuat one hot encode)
7. run training.py (melatih data di database skripsi dengan metode Skip-Gram)
8. run trainingcbow.py (melatih data di database skripsi dengan metode CBOW)(in-progress)
