import os

class exportToJSON:
    """docstring for exportToJSON."""

    def __init__(self):
        super(exportToJSON, self).__init__()

    def dumpdata(self, pairs):
        if os.path.exists(os.path.join(os.getcwd(), 'extra')):
                pass
        else:
                os.makedirs('extra')
        my_data = pairs.to_json('extra/database.json', orient='index')

class exportToCSV:
    """docstring for exportToCSV."""

    def __init__(self):
        super(exportToCSV, self).__init__()

    def dumpdata(self, pairs):
        if os.path.exists(os.path.join(os.getcwd(), 'extra')):
                pass
        else:
                os.makedirs('extra')
        my_data = pairs.to_csv('extra/database.csv', index=False)
