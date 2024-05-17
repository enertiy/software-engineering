import re
import pandas
from py2neo import Graph
from py2neo import Node
from py2neo import Relationship
from py2neo import NodeMatcher


MAX_FILM_NUM = 250
MAX_ACTOR_NUM = 100


# 查询节点
def match_node(graph, label, attrs, primary_key):
    n="_."+primary_key+"=\""+attrs[primary_key] + "\""
    matcher = NodeMatcher(graph)
    return matcher.match(label).where(n).first()


# 建立一个节点
def create_node(graph, label, attrs, primary_key):
    # 查询是否已经存在，若存在则返回节点，否则返回None
    value = match_node(graph, label, attrs, primary_key)
    # 如果要创建的节点不存在则创建
    if value is None:
        node = Node(label, **attrs)
        n = graph.create(node)
        return n
    return None


if __name__ == '__main__':
    # 连接本地的 Neo4j 数据库，地址为 127.0.0.1，http 端口默认为 7474，用户名和密码分别为 neo4j 与 12345678
    graph = Graph("bolt: // localhost:7687", auth=("neo4j", "12345678"))

    # 清空neo4j图数据库
    graph.delete_all()

    # 读取节点表，并加入neo4j图数据库
    data = pandas.read_csv("./data/movie.csv").fillna("")
    for i in range(MAX_FILM_NUM):
        # 电影节点
        film_title = re.compile(r"[\u4e00-\u9fff]+").findall(data.loc[i, 'title'])[0]
        create_node(graph, "电影", {"name": film_title, "desc": data.loc[i, 'introduction']},"name")

        # 导演节点
        director_list = data.loc[i, 'director'].split("/")
        for director in director_list:
            create_node(graph, "导演", {"name": director}, "name")
            director_rel = Relationship(graph.nodes.match(name=film_title).first(),
                                  "导演",
                                  graph.nodes.match("导演", name=director).first())
            graph.create(director_rel)

        # 编剧节点
        creator_list = data.loc[i, 'creator'].split("/")
        for creator in creator_list:
            create_node(graph, "编剧", {"name": creator}, "name")
            creator_rel = Relationship(graph.nodes.match(name=film_title).first(),
                                  "编剧",
                                  graph.nodes.match("编剧", name=creator).first())
            graph.create(creator_rel)

        # 主演节点
        actor_list = data.loc[i, 'actor'].split("/")
        for j in range(min(MAX_ACTOR_NUM,len(actor_list))):
            actor=actor_list[j]
            create_node(graph, "主演", {"name": actor}, "name")
            actor_rel = Relationship(graph.nodes.match(name=film_title).first(),
                                  "主演",
                                  graph.nodes.match("主演", name=actor).first())
            graph.create(actor_rel)

        # 类型节点
        type_list = data.loc[i, 'type'].split("/")
        for type in type_list:
            create_node(graph, "类型", {"name": type}, "name")
            type_rel = Relationship(graph.nodes.match(name=film_title).first(),
                               "类型",
                               graph.nodes.match("类型", name=type).first())
            graph.create(type_rel)

        # 制片国家/地区节点
        location_list = data.loc[i, 'country/location'].split("/")
        for location in location_list:
            create_node(graph, "制片国家/地区", {"name": location}, "name")
            location_rel = Relationship(graph.nodes.match(name=film_title).first(),
                               "制片国家/地区",
                               graph.nodes.match("制片国家/地区", name=location).first())
            graph.create(location_rel)

        # 语言节点
        language_list = data.loc[i, 'language'].split("/")
        for language in language_list:
            create_node(graph, "语言", {"name": language}, "name")
            language_rel = Relationship(graph.nodes.match(name=film_title).first(),
                               "语言",
                               graph.nodes.match("语言", name=language).first())
            graph.create(language_rel)

        # 制片年份节点
        year = data.loc[i, 'dates'].split("-")[0]
        create_node(graph, "制片年份", {"year": year}, "year")
        year_rel = Relationship(graph.nodes.match(name=film_title).first(),
                                "制片年份",
                                graph.nodes.match("制片年份", year=year).first())
        graph.create(year_rel)

        # 评分节点
        mark = str(data.loc[i, 'mark'])
        create_node(graph, "评分", {"mark": mark}, "mark")
        mark_rel = Relationship(graph.nodes.match(name=film_title).first(),
                            "评分",
                            graph.nodes.match("评分", mark=mark).first())
        graph.create(mark_rel)
