function sendAction(action) {
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: action }),
    })
        .then((response) => response.json())
        .then((data) => {
            document.getElementById('result').textContent = data.result ?? "Error";
            document.getElementById('expression').textContent = "Expresión: " + data.expression;
        })
        .catch((error) => console.error('Error:', error));
}
