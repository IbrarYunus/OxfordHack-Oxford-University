var dates = [];
var config = {
    type: 'line',
    data: {
        labels: Array.from(new Set(dates)).sort(),
        datasets: [{
            label: "Money Spent",
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 0.2)',
            data: [],
            fill: false,
        }]
    },
    options: {
        responsive: true,
        title:{
            display:true,
            text:'$$$£££'
        },
        tooltips: {
            mode: 'index',
            intersect: false,
        },
        hover: {
            mode: 'nearest',
            intersect: true
        },
        scales: {
            xAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Date'
                }
            }],
            yAxes: [{
                display: true,
                scaleLabel: {
                    display: true,
                    labelString: 'Amount'
                }
            }]
        }
    }
};
window.onload = function() {
    var ctx = document.getElementById("myChart").getContext("2d");
    var resetBtn = document.getElementById("resetData");
    resetBtn.addEventListener("click", function() {
        // config.data.datasets.data = [];
        // config.data.labels = [];
        // console.log("done");
        // window.myLine.update();
        config.data.labels = []; // remove the label first
            config.data.datasets[0].data = [];
            
        window.myLine.update();
    });
    window.myLine = new Chart(ctx, config);

    var myDropzone = new Dropzone("div#imageupload", { url: "http://66fad73c.ngrok.io/api/test",paramName:'image',uploadMultiple:false});

    myDropzone.on("success", function(file,data) {
        /* Maybe display some more file information on your page */
        console.log(data);
        addPoints(data);
        myDropzone.removeFile(file);
    });
};
function addPoints(data) {
    if (config.data.datasets.length > 0) {
        var money = Number(data.split(" ")[1]);
        var date = data.split(" ")[2];
        if (config.data.labels.indexOf(date) > -1) {
            config.data.labels.forEach(function(data, idx) {
                if (data === date) {
                    // updateQuery(date, money);
                    config.data.datasets[0].data[idx] += money;
                }
            });
        } else {
            console.log(date);
            config.data.labels.push(date);
            config.data.labels.sort();
            var valueIndex = config.data.labels.indexOf(date);
            console.log(config.data.datasets[0].data);
            config.data.datasets[0].data.splice(valueIndex, 0, money);
        }
        window.myLine.update();

    }
};
