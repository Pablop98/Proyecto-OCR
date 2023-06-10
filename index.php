<?php

$servidor = "localhost";
$usuario = "root";
$contrasena = "";
$bdd = "MiBaseDeDatos";

// Crear conexión
$conexion = new mysqli($servidor, $usuario, $contrasena, $bdd);

// Verificar la conexión
if ($conexion->connect_error) {
    die("Error de conexión: " . $conexion->connect_error);
}

?>

<html>
<head>
    <meta http-equiv='refresh' content='3'>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
        }

        h1,
        h2 {
            margin-top: 30px;
            font-size: 150%;
            text-align: center;
            padding: 10px;
            background-color: #246355;
            color: white;
            border-radius: 10px;
            width: 25%;
        }

        .primeraTabla {
            width: 30%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: white;
            table-layout: fixed;
        }

        table {
            background-color: white;
            border-collapse: collapse;
            width: 60%;
        }

        td {
            padding: 10px;
            text-align: center;
        }

        th {
            background-color: #246355;
            font-weight: bold;
            border-bottom: 5px solid #0F362D;
            color: white;
            padding: 10px;
            text-align: center;
        }

        tr:nth-child(even) {
            background-color: #ddd;
        }

        tr:hover td {
            background-color: #369681;
            color: white;
        }
    </style>
</head>
<body>

<?php
// Consulta SQL para obtener los datos de la tabla Coche ordenados por fecha y hora de más reciente a más antiguo
$consulta = "SELECT * FROM Coche ORDER BY fecha DESC, hora DESC";
$resultado = $conexion->query($consulta);

echo "<h1>Registro de coches actuales</h1>";

if ($resultado->num_rows > 0) {
    echo "<table class='primeraTabla'>";
    echo "<tr><th>Matrícula</th><th>Hora</th><th>Fecha</th></tr>";

    // Mostrar los datos en la tabla
    while ($fila = $resultado->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $fila["matricula"] . "</td>";
        echo "<td>" . $fila["hora"] . "</td>";
        echo "<td>" . $fila["fecha"] . "</td>";
        echo "</tr>";
    }

    echo "</table>";
} else {
    echo "<p>No se encontraron resultados.</p>";
}

// Consulta SQL para obtener los datos de la tabla CocheSalida ordenados por fecha y hora de más reciente a más antiguo
$consulta2 = "SELECT matricula, horaEntrada, horaSalida, fechaEntrada, fechaSalida FROM CocheSalida ORDER BY fechaEntrada DESC, horaEntrada DESC";
$resultado2 = $conexion->query($consulta2);

echo "<h2>Registro de salidas</h2>";

if ($resultado2->num_rows > 0) {
    echo "<table>";
    echo "<tr><th>Matrícula</th><th>Hora de entrada</th><th>Hora de salida</th><th>Fecha de entrada</th><th>Fecha de salida</th></tr>";

    // Mostrar los datos en la tabla
    while ($fila2 = $resultado2->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $fila2["matricula"] . "</td>";
        echo "<td>" . $fila2["horaEntrada"] . "</td>";
        echo "<td>" . $fila2["horaSalida"] . "</td>";
        echo "<td>" . $fila2["fechaEntrada"] . "</td>";
        echo "<td>" . $fila2["fechaSalida"] . "</td>";
        echo "</tr>";
    }

    echo "</table>";
} else {
    echo "<p>No se encontraron resultados.</p>";
}

echo "</body>";
echo "</html>";

// Cerrar la conexión
$conexion->close();
?>

