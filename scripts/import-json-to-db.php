<?php

$data_directory = 'json-data';
$files = array_diff(scandir($data_directory), ['..', '.']);
$files_count = count($files);

// Separar os dados em lotes para evitar problemas de memoria, timeout, etc
$offset = 0;
$limit = 500;
$files_chunk = array_slice($files, $offset, $limit);

$db_host = 'localhost';
$db_name = 'movemos';
$db_user = 'root';
$db_pwd = 'root';
$db = new PDO("mysql:host=$db_host;dbname=$db_name;charset=utf8mb4", $db_user, $db_pwd);

foreach ($files_chunk as $file_key => $file) {
  print ($offset + $file_key + 1) . '/' . $files_count . "\n";
  $json = json_decode(file_get_contents($data_directory . '/' . $file));

  foreach ($json->DATA as $key => $registro) {
    $sql = "INSERT INTO posicoes (DATAHORA, ORDEM, LINHA, LATITUDE, LONGITUDE, VELOCIDADE)
            VALUES (:datahora,:ordem,:linha,:lat,:long,:velocidade)";

    $stmt = $db->prepare($sql);
    $stmt->execute([
      ':datahora' => DateTime::createFromFormat(
        'm-d-Y H:i:s', trim($registro[0])
      )->getTimestamp(),
      ':ordem' => $registro[1],
      ':linha' => $registro[2],
      ':lat' => $registro[3],
      ':long' => $registro[4],
      ':velocidade' => $registro[5]
    ]);
    if (
      !empty($stmt->errorInfo()[1])
      && $stmt->errorInfo()[1] != 1062 // Ignorar chaves duplicadas
    ) {
      print_r($stmt->errorInfo());
    }
  }
}