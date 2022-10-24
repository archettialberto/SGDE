if __name__ == "__main__":

    import requests

    my_task = {
        'task_name': 'handwritten_digits',
        'description': 'Classification of handwritten digits.',
        'labels': '0;1;2;3;4;5;6;7;8;9',
    }

    my_gen = {
        'task_id': 1,
        'params': str({'w': [0.5, -4, 0], 'b': 0.01}),
    }

    # x = requests.post('http://127.0.0.1:5000/tasks', data=my_task)
    # x = requests.get('http://127.0.0.1:5000/tasks')
    # x = requests.get('http://127.0.0.1:5000/tasks/999')
    # x = requests.get('http://127.0.0.1:5000/tasks/1')

    # x = requests.post('http://127.0.0.1:5000/tasks/1/generators', data=my_gen)
    # x = requests.get('http://127.0.0.1:5000/tasks/1/generators')
    # x = requests.get('http://127.0.0.1:5000/tasks/999/generators')
    # x = requests.get('http://127.0.0.1:5000/tasks/1/generators/999')
    x = requests.get('http://127.0.0.1:5000/tasks/1/generators/1')
    print(x.text)
