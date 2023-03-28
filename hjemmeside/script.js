const titles = ["temperature", "humidity", "wind", "pressure"];
let ctxs = [];

for (const title of titles) {
    ctxs.push(document.getElementById(title));
}

// const chart = new Chart(ctxs[0], {
//     type: 'line',
//     data: data,
//     options: {
//         scales: {
//             x: {
//                 type: 'time',
//                 time: {
//                     unit: 'hour'
//                 }
//             }
//         }
//     }
// });

function combined(element) {
    return { x: moment(element.time), y: element.temperature }
}

async function main() {
    let res = await fetch("http://127.0.0.1:5001/Eagle_River")
    res = await res.json()
    temperatureList = res.map(e => combined(e))
    console.log(temperatureList)
    const chart = new Chart(ctxs[0], {
        type: 'line',
        data: {
            datasets: [{
                data: temperatureList
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'hour'
                    }
                }
            }
        }
    });
    console.log(chart.data)
}

main()
