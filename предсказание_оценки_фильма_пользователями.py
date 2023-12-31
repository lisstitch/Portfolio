# -*- coding: utf-8 -*-
"""Предсказание оценки фильма пользователями.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GqqWlXoJg85xLYUfvPOC7w1_seRV6J47

Загрузите в колаб файлы по оценкам (ratings) и фильмам (movies) и создайте на их основе pandas-датафреймы
"""

import pandas as pd

df_ratings = pd.read_csv("u.data.csv")

df_movies = pd.read_csv("u.item.csv")

"""Средствами Pandas, используя dataframe ratings, найдите id пользователя, поставившего больше всего оценок


"""

df_ratings.columns

df_movies.columns

df_ratings_1 = df_ratings.groupby('user id')

df_ratings_1 = df_ratings_1['rating'].count()

df_ratings_1.max()

df_ratings_1.sort_values()

"""Оставьте в датафрейме ratings только те фильмы, который оценил данный пользователь"""

df_ratings_2 = df_ratings.loc[df_ratings['user id'] == 405]

df_ratings_2

"""Добавьте к датафрейму из задания 3 столбцы:

- По жанрам. Каждый столбец - это жанр. Единицу записываем, если фильм принадлежит данному жанру и 0 - если нет

- Cтолбцы с общим количеством оценок от всех пользователей на фильм и суммарной оценкой от всех пользователей

"""

df_merge = df_ratings_2.merge(df_movies, left_on = 'item id', right_on = 'movie id ', how = 'inner')

df_ratings_4 = df_ratings.groupby('item id')

df_ratings_4 = df_ratings_4['rating'].count()

df_ratings_4

df_ratings_5 = df_ratings.groupby('item id')

df_ratings_5 = df_ratings_5['rating'].sum()

df_ratings_5

df_merge_2 = df_merge.merge(df_ratings_4, left_on = 'item id', right_on = 'item id', how = 'inner')

df_merge_3 = df_merge_2.merge(df_ratings_5, left_on = 'item id', right_on = 'item id', how = 'inner')

df_merge_3

df_merge_3.columns

df_merge_3.rename(columns = {'rating_x':'rating', 'rating_y':'rating count', 'rating':'rating sum'}, inplace = True)

df_merge_3

"""Сформируйте X_train, X_test, y_train, y_test"""

from sklearn.model_selection import train_test_split

df_merge_3.columns

X, y = df_merge_3[["user id", "item id", "rating", "unknown", "Action",
       "Adventure", "Animation", "Children's", "Comedy", "Crime",
       "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
       "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western",
       "rating count"]], df_merge_3["rating sum"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

"""Возьмите модель линейной регрессии (или любую другую для задачи регрессии)  и обучите ее на фильмах"""

from sklearn.linear_model import LinearRegression

lr = LinearRegression()

lr.fit(X_train, y_train)

"""Оцените качество модели на X_test, y_test при помощи метрик для задачи регрессии"""

from sklearn.metrics import mean_squared_error

lr.predict(X_test)

mean_squared_error(y_test, lr.predict(X_test))

mean_squared_error(y_train, lr.predict(X_train))

"""Средствами спарка вывести среднюю оценку для каждого фильма"""

!apt-get update

!apt-get install openjdk-8-jdk-headless -qq > /dev/null

!wget -q https://downloads.apache.org/spark/spark-3.2.3/spark-3.2.3-bin-hadoop2.7.tgz

!tar -xvf spark-3.2.3-bin-hadoop2.7.tgz

!pip install -q findspark

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.2.3-bin-hadoop2.7"

import findspark
findspark.init()
from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[*]").getOrCreate()

df_ratings_spark = spark.read.csv('u.data.csv', inferSchema=True, header=True)

df_movies_spark = spark.read.csv('u.item.csv', inferSchema=True, header=True)

df_ratings_spark.columns

df_movies_spark.columns

"""Посчитайте средствами спарка среднюю оценку для каждого жанра"""

df_ratings_avg = df_ratings_spark.groupBy('item id').avg('rating')

df_ratings_avg.show()

df_ratings_avg = df_ratings_avg.withColumnRenamed('item id', 'item_id')

df_ratings_avg.show()

"""В спарке получить 2 датафрейма с 5-ю самыми популярными и самыми непопулярными фильмами (по количеству оценок, либо по самой оценке - на Ваш выбор)"""

df_ratings_spark = df_ratings_spark.withColumnRenamed('item id', 'item_id')

df_movies_spark = df_movies_spark.withColumnRenamed('movie id ', 'movie_id')

df_ratings_movies = df_ratings_spark.join(df_movies_spark, df_ratings_spark.item_id == df_movies_spark.movie_id, how = 'inner')

df_ratings_movies.show()

df_join_avg = df_ratings_movies.join(df_ratings_avg, df_ratings_movies.item_id == df_ratings_avg.item_id, how = 'inner')

df_join_avg.show(10)

df_popular = df_join_avg.sort('avg(rating)', ascending=True).show(5)

df_unpopular = df_join_avg.sort('avg(rating)', ascending=False).show(5)