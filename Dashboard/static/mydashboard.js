var data_API_1, data_API_2;
var name_API_1, name_API_2;
var titre_1, titre_2;

 // Chargement des données
 $.ajax({
          url: "/API/radar/",
          success: import_data
        });


function import_data(result) {
	data_API_1 = result["data_1"];
	name_API_1 = result["name_1"];
	data_API_2 = result["data_2"];
	name_API_2 = result["name_2"];
	titre_1 = result["titre_1"];
	titre_2 = result["titre_2"];
	display_radar('container_1', titre_1, data_API_1, name_API_1);
    display_radar('container_2', titre_2, data_API_2, name_API_2);
                                }

function display_radar(container, titre, data_API, name_API) {

Highcharts.chart(container, {
    title: {
        text: titre
            },
    chart: {
        polar: true,
        type: 'area'
            },
    plotOptions: {
            column: {
                colorByPoint: true
                    }
                },
    colors: [
            '#0FE248',
            '#E61B4D',
            '#3F6EF5'],
    xAxis: {
        categories: name_API,
        tickmarkPlacement: 'on',
        lineWidth: 0
            },
    yAxis: {
        gridLineInterpolation: 'polygon',
        lineWidth: 0,
        min: 0
            },
    tooltip: {
        shared: true,
        pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:,.0f}</b><br/>'
            },
    legend: {
        align: 'right',
        verticalAlign: 'middle',
        layout: 'vertical'
            },
    series: [{
        name: 'Accepté',
        data: data_API['0'],
        pointPlacement: 'on',
        fillColor: '#0FE248',
        opacity: 0.3
            }, {
        name: 'Refusé',
        data: data_API['1'],
        pointPlacement: 'on',
        fillColor: '#E61B4D',
        opacity: 0.3
            },{
        name: 'Client',
        data: data_API['2'],
        pointPlacement: 'on',
        fillColor: '#3F6EF5',
        opacity: 0.3
            }],
})};