const data = {
    labels: labels,
    datasets: [],
};

const config = {
    type: 'line',
    data: data,
    options: {
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
            },
        },
        scales: {
            y: {
                min: 0,
                title: {
                    display: true,
                    text: "HUF",
                }
            },
        }
    },
};

const myChart = new Chart(
    document.getElementById('myChart'),
    config,
);


function addToDataset(code) {
    for (var i = 0; i<dataset.length; i++) {
        if(code == dataset[i].code) {
            myChart.data.datasets.push(dataset[i]);
            myChart.update();
            break;
        }
    }
}


function removeFromDataset(code) {
    myChart.data.datasets = myChart.data.datasets.filter(function(obj) {
        return (obj.code != code);
    });
    myChart.update();
}


function onClick() {
    var code = this.dataset.code;
    if(this.dataset.status == "active") {
        removeFromDataset(code);
        var target = "inactive-datasets";
        this.dataset.status = "inactive";
    } else {
        addToDataset(code);
        var target = "active-datasets";
        this.dataset.status = "active";
    }

    this.remove();

    var fragment = document.createDocumentFragment();
    fragment.appendChild(this);
    document.getElementById(target).appendChild(fragment);

}

// adds the onClick event listener to all the pills
var elements = document.getElementsByClassName("label-pill")
for (var i = 0; i < elements.length; i++) {
    elements[i].addEventListener("click", onClick);
}

// adds the products show on page load
var initialCodes = [14110, 14107, 13305];
for (var i = 0; i<initialCodes.length; i++) {
    document.querySelector('[data-code="' + initialCodes[i] + '"]').click();
}
