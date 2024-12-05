let expression = "";


function sendAction(action) {
    if (action === 'borrar') {
        expression = expression.slice(0, -1);
    } else if (action === 'limpiar') {
        expression = "";
    } else if (action === 'MS') {
        const memoryValue = document.getElementById('result').textContent;
        if (memoryValue && memoryValue !== "Error") {
            expression += memoryValue;
        } else {
            alert("No hay valor en memoria para usar.");
        }
    } else {
        expression += action;
    }

    updateDynamicExpression();
}

function updateDynamicExpression() {
    const dynamicExpressionDiv = document.getElementById('dynamic-expression');
    dynamicExpressionDiv.textContent = `Expresión dinámica: ${expression}`;
}


function sendExpression() {
    console.log(JSON.stringify({ action: "=", expression: expression }))
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: "=", expression: expression }),
    })
        .then((response) => response.json())
        .then((data) => {
            document.getElementById('result').textContent = data.result ?? "Error";
            document.getElementById('expression').textContent = "Expresión: " + expression;

            const classificationsList = document.getElementById('classifications');
            classificationsList.innerHTML = '';
            data.classifications.forEach((classification) => {
                const listItem = document.createElement('li');
                listItem.textContent = classification;
                classificationsList.appendChild(listItem);
            });

            if (data.tree) {
                drawTree(data.tree);
            }

            expression = "";
            updateDynamicExpression();
        })
        .catch((error) => console.error('Error:', error));
}

function drawTree(treeData) {
    const width = 600;
    const height = 500;

    d3.select("#tree").html("");

    const svg = d3.select("#tree")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const treeLayout = d3.tree().size([width - 100, height - 100]);
    const root = d3.hierarchy(treeData);

    treeLayout(root);

    svg.selectAll('line')
        .data(root.links())
        .enter()
        .append('line')
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)
        .attr('stroke', '#000');

    svg.selectAll('circle')
        .data(root.descendants())
        .enter()
        .append('circle')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', 25)
        .attr('fill', '#fca311');

    svg.selectAll('text')
        .data(root.descendants())
        .enter()
        .append('text')
        .attr('x', d => d.x)
        .attr('y', d => d.y)
        .attr('dy', 10)
        .attr('dx', -10)
        .text(d => d.data.name);
}



