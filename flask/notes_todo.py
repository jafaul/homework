
# todo geeks for geek (data structer, algorithms courses), leetcode.com, tcp/ip geek for geeks

# todo check bootstrap, progit(3 глави), jinja2, djangogirls, geek for geeks: coupling and cohesion

# todo read flask doc, pep8, /TCP-IP Illustrated Volunme 1-The Protocols.pdf

#  0 форма
   #  нет порядка строк и столбцов(2)

# 1 нормальная форма:
#    3. нет одинаковых строк
#    4. каждое пересечение колонки и столбца содержит только одно значение (в ячейке только одно значение)
#     5. в каждой ячейке только одно атомарное значение
#     6. в столбце данные одного типа
# 2 нормальная форма
 #     в таблицу не можно быть данных которые можно получить зная только половину ключа
# 3 нормальная форма зависят от значения других неключевых столбцов)
       # ни одна колонка не может быть выведена из другой колонки (например колонка ребенок и колонка год рождения это нарушение)
##############################################333#333

# усиленный вариант 3нф Boyce-Codd Normal Form (BCNF)
       # каждый атрибут зависит от одного супер ключа
# 4 nf
   # нетривиальная многозначная зависимость
# 5 nf (нужно углубляться в специфику исходных данных)
# 6 nf для хронологических бд
# де нормализация для ускорения в крайнем случае)