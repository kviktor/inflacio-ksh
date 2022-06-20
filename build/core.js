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


function updateHash(action, code) {
    var hash = window.location.hash;
    var hashCodes = hash ? window.location.hash.substring(1).split(",") : [];
    if(action == "add" && hashCodes.indexOf(code) == -1) {
        hashCodes.push(code);
    } else if (action == "remove") {
        hashCodes = hashCodes.filter(function(item) {
            return item !== code
        });
    }

    newHash = hashCodes.toString()
    window.location.hash = newHash;

    var navIds = ["nav-yearly", "nav-monthly"];
    for(var i=0; i<navIds.length; i++) {
        var aTag = document.getElementById(navIds[i]).getElementsByTagName("a")[0];
        var parts = aTag.href.split(".html");
        aTag.href = parts[0] + ".html#" + newHash;
    }
}


function addToDataset(code) {
    for (var i = 0; i<dataset.length; i++) {
        if(code == dataset[i].code) {
            myChart.data.datasets.push(dataset[i]);
            myChart.update();
            updateHash("add", code);
            break;
        }
    }
}


function removeFromDataset(code) {
    myChart.data.datasets = myChart.data.datasets.filter(function(obj) {
        return (obj.code != code);
    });
    myChart.update();
    updateHash("remove", code);
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


function initialize() {
    var hash = window.location.hash;
    if(hash) {
        var initialCodes = hash.substring(1).split(",");
    } else {
        var initialCodes = [14110, 14107, 13305];
    }

    for (var i = 0; i<initialCodes.length; i++) {
        document.querySelector('[data-code="' + initialCodes[i] + '"]').click();
    }
}

initialize();
