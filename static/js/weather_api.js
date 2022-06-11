$(document).ready(function () {
    get_weather_from_server();
});

const get_weather_from_server = () => {
    $.ajax({
        type: 'GET',
        url: '/weather',
        data: {},
        success: function (response) {
            const show_datas = response['show_datas'];
            const location = show_datas[0];
            const weather = show_datas[1];
            const temp = Math.floor(show_datas[2]);


            const weather_html = `<div id="weather">
                                    <span>현재 위치: ${location} /</span>
                                    <span>현재 날씨: ${weather} /</span>
                                    <span>현재 기온: ${temp}℃</span>
                                </div>`;

            $('#weather_container').append(weather_html);
        }
    })
};
