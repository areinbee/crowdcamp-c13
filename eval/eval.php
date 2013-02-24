<?php

require_once('parsecsv.lib.php');
$evalResultsFile = "evalResults-test.csv";

$itemSubmitted;
// if results were submitted, store them
if (isset($_REQUEST['item'])) {
  $itemSubmitted = $_REQUEST['item'];
  $scoreOverall = $_REQUEST['scoreOverall'];
  $fh = fopen($evalResultsFile, "a");
  fwrite($fh, $itemSubmitted . "," . $scoreOverall . "\n");
  fclose($fh);
}






// array with [itemID]['html'] => html representation of the item
// array with [itemID]['N'] => number of evaluations already collected
$itemsToEval = array();
$itemsToEval['key1']['html'] = "Summary of story 1.";
$itemsToEval['key2']['html'] = "Summary of story 2.";

# read CSV data
$evalResults = new parseCSV();
$evalResults->auto($evalResultsFile);

// count how many evaluations we have for each item
foreach($evalResults->data as $row) {
  $itemsToEval[$row['item']]['N'] += 1;
}

// find item with fewest evals
$minItem;
$minN = 1000;
foreach($itemsToEval as $itemID => $item) {
  if ($item['N'] < $minN) {
    $minN = $item['N'];
    $minItem = $itemID;
  }
}


?>

<html>
<head>
<link rel="stylesheet" href="bootstrap.min.css" type="text/css">

</head>

<body>

<?php echo "item: " . $itemSubmitted ?><br/>

<h1>Evaluate this story concept</h1>
<p>Read the story summary below.  Tell us how good you think it is.</p>

<div class="well">
<?php 
echo $itemsToEval[$minItem]['html'];
?>
</div>

<form class="form-horizontal" action="eval.php">
<input type="hidden" name="item" value="<?php echo $minItem ?>"/>
<label>How good do you think this story is overall? 
<select name="scoreOverall">
<option value="na"></option>
<option value="1">1 - not at all</option>
<option value="2">2</option>
<option value="3">3</option>
<option value="4">4</option>
<option value="5">5 - fantastic</option>
</select>
</label>

<button type="submit" class="btn btn-primary">Submit</button>
</form>

</body>
</html>