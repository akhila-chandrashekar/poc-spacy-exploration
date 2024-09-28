# import json
from datetime import datetime

# import pandas
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flasgger import Swagger
from processor._exportPairs import exportToJSON
from processor._getentitypair import GetEntity
from processor._graph import GraphEnt
from processor._qna import QuestionAnswer
from database.__db_ingestion import Neo4jDBHandler

app = Flask(__name__)
swagger = Swagger(app)

class CheckAndSave:
    """docstring for CheckAndSave."""

    def __init__(self):
        super(CheckAndSave, self).__init__()

    def createdataset(self, para, que, ent, ans1, ans2):

        wholedata = {"para":[str(para)],"que":[[str(que)]], "entities":[ent], "ans1": [ans1], "ans2":[ans2]}
        # print(wholedata)
        # return None

class OurModel:
    def __init__(self):
        self.getent = GetEntity()
        self.qa = QuestionAnswer()
        self.export = exportToJSON()
        self.graph = GraphEnt()
        self.db = Neo4jDBHandler()

    def getAnswer(self, paragraph, question):

        refined_text = self.getent.preprocess_text([paragraph])
        dataEntities, numberOfPairs = self.getent.get_entity(refined_text)

        if dataEntities:
            # data_in_dict = dataEntities[0].to_dict()
            self.export.dumpdata(dataEntities[0])
            outputAnswer = self.qa.findanswer(str(question), numberOfPairs)
            if outputAnswer == []:
                return None
            return outputAnswer
        return None

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('index.html')

@app.route('/clear', methods=['GET', 'POST'])
def clear():
    return redirect(url_for('main'))

# @app.route('/select', methods=['GET', 'POST'])
# def select():
#     return jsonify(result={"titles" : titles, "contextss" : contextss, "context_questions" : context_questions})

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    # model1 = MachineComprehend()
    model2 = OurModel()
    save = CheckAndSave()
    # if request.form["clear"] == 'clear':
    #     return redirect('/')
    input_paragraph = str(request.form["paragraph"])
    input_question = str(request.form["question"])
    # bidaf_answer = model1.answer_question(input_paragraph, input_question)
    my_answer = model2.getAnswer(input_paragraph, input_question)

    # save.createdataset(input_paragraph, input_question, data_in_dict, my_answer, bidaf_answer)

    return render_template('index.html', my_answer=my_answer, input_paragraph=input_paragraph ,input_question=input_question)

@app.route('/persons', methods=['GET'])
def get_all_persons():
    model2 = OurModel()
    input_node_name = request.args.get('node', default='', type=str)
    input_relationship = request.args.get('relationship', default='', type=str)
    records = model2.db.selectAll(input_node_name, input_relationship)
    result = []
    for record in records:
        node1 = record['n']
        relationship = record['r']
        node2 = record['m']
        
        result.append({
            "source": {
                "id": node1.element_id,  # Element ID of the source node
                "name": node1['name'],
                "labels": list(node1.labels)
            },
            "relationship": {
                "type": relationship.type,
                "properties": dict(relationship)
            },
            "target": {
                "id": node2.element_id,  # Element ID of the target node
                "name": node2['name'],
                "labels": list(node2.labels)
            }
        })

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=20550, threaded=True, debug=True)
