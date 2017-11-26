var mysql = require('mysql');

var connection = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'password',
    database: 'moneyTracker'
});

connection.connect();

function updateQuery(date, money) {
    connection.query('UPDATE moneyTracker SET money = ' + money + ' WHERE date = ' + date, function(err, result) {
        
    });
}