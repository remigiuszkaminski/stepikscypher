from flask import Flask, jsonify, request

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

uri = os.getenv('URI')
driver = GraphDatabase.driver(uri, auth=(
    'neo4j', '12345678'), database="neo4j")


@app.route('/test', methods=['GET'])
def test():
    return "Hello World"


@app.route('/employees', methods=['GET'])
async def get_employees(sort=None, filtr=None, filteredAttribute=None):
    employees = []
    with driver.session() as session:
        if (filtr != None and sort != None):
            result = session.run(
                f"MATCH (e:Employee) WHERE e.{filteredAttribute} CONTAINS '{filtr}' RETURN e ORDER BY e.{sort}")
        elif (filtr != None and sort == None):
            result = session.run(
                f"MATCH (e:Employee) WHERE e.{filteredAttribute} CONTAINS '{filtr}' RETURN e")
        elif (sort != None and filtr == None):
            result = session.run(
                f"MATCH (e:Employee) RETURN e ORDER BY e.{sort}")
        else:
            result = session.run("MATCH (e:Employee) RETURN e")
        for record in result:
            employees.append(dict(record['e']))
    return jsonify(employees)


@app.route('/employees', methods=['POST'])
async def create_employee(employee):
    if employee.departament == None:
        return (
            f"Employee {employee['name']} must have a departament"
        )
    with driver.session() as session:
        result = session.run(
            f"MATCH (e:Employee) WHERE e.name = '{employee['name']}' RETURN e")
        if (len(list(result)) > 0):
            return "Employee already exists"
    with driver.session() as session:
        result = session.run(
            f"CREATE (e:Employee) SET e = {employee} RETURN e")
    return (
        f"Employee {employee['name']} created successfully"
    )


@app.route('/employees/<id>', methods=['PUT'])
async def update_employee(id, employee):
    with driver.session() as session:
        result = session.run(
            f"MATCH (e:Employee) WHERE e.id = '{id}' RETURN e")
        if (len(list(result)) == 0):
            return "Employee doesn't exist"
    with driver.session() as session:
        result = session.run(
            f"MATCH (e:Employee) WHERE e.id = '{id}' SET e = {employee} RETURN e")
    return (
        f"Employee {employee['name']} updated successfully"
    )


@app.route('/employees/<id>', methods=['DELETE'])
async def delete_employee(id):
    with driver.session() as session:
        result = session.run(
            f"MATCH (e:Employee) WHERE e.id = '{id}' RETURN e")
        if (len(list(result)) == 0):
            return "Employee doesn't exist"
    with driver.session() as session:
        result = session.run(
            f"MATCH (e:Employee) WHERE e.id = '{id}' DETACH DELETE e")
    return (
        f"Employee deleted successfully"
    )


@app.route('/employees/<id>/subordinates', methods=['GET'])
async def get_subordinates(id):
    subordinates = []
    with driver.session() as session:
        result = session.run(
            f"MATCH (e:Employee)-[:MANAGES]->(s:Employee) WHERE e.id = '{id}' RETURN s")
        for record in result:
            subordinates.append(dict(record['s']))
    return jsonify(subordinates)


@app.route('/employeeDepartament/<id>', methods=['GET'])
async def get_employee_departament(id):
    with driver.session() as session:
        departament = session.run(
            f"MATCH (e:Employee)-[:WORKS_IN]->(d:Departament) WHERE e.id = '{id}' RETURN d")

        amount = session.run(
            f"MATCH (e:Employee)-[:WORKS_IN]->(d:Departament) WHERE d.name = {departament}' RETURN COUNT(e)")
    return jsonify(departament, amount)


@app.route('/departaments', methods=['GET'])
async def get_departaments():
    departaments = []
    with driver.session() as session:
        result = session.run("MATCH (d:Departament) RETURN d")
        for record in result:
            departaments.append(dict(record['d']))
    return jsonify(departaments)


@app.route('/departaments/<id>/workers', methods=['GET'])
async def get_workers(id):
    workers = []
    with driver.session() as session:
        result = session.run(
            f"MATCH (e:Employee)-[:WORKS_IN]->(d:Departament) WHERE d.id = '{id}' RETURN e")
        for record in result:
            workers.append(dict(record['e']))
    return jsonify(workers)


if __name__ == '__main__':
    app.run()