<?php

require_once('parsecsv.lib.php');
$evalResultsFile = "evalResults-test.csv";

$scoreFields = array('scoreOverall', "scoreSurprise", "scoreCharacter", "scorePlot", "scoreBelievable");

$itemSubmitted;
// if results were submitted, store them
if (isset($_REQUEST['item'])) {
  $itemSubmitted = $_REQUEST['item'];
  $fh = fopen($evalResultsFile, "a");
  fwrite($fh, $itemSubmitted);
  for($i = 0; $i< count($scoreFields); $i++)
    fwrite($fh, "," . $_REQUEST[$scoreFields[$i]]);
  fwrite($fh, "\n");
  fclose($fh);
}


$fileNames = array("stories/zombies.html");

// array with [itemID]['html'] => html representation of the item
// array with [itemID]['N'] => number of evaluations already collected
$itemsToEval = array();

foreach($fileNames as $fname)
  $itemsToEval[$fname]['html'] = file_get_contents($fname);

//echo $fname .<br/>

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
<style>
body {
    margin: 20px;
}
</style>
</head>

<body>

<!-- <?php echo "item: " . $fname ?><br/> -->

<h1>Evaluate this story concept</h1>
<p>Read the story summary below.  
It is presented in the form of yes/no questions.  Try to imagine what the complete story would look like.
Tell us how much potential it has.</p>

<div class="well">
<?php 
echo $itemsToEval[$minItem]['html'];
?>
</div>

<form class="form-horizontal" action="eval.php">
<input type="hidden" name="item" value="<?php echo $minItem ?>"/>

<label>How surprising is this story? 
<select name="scoreSurprise">
<option value="na"></option>
<option value="1">1 - not at all</option>
<option value="2">2</option>
<option value="3">3</option>
<option value="4">4</option>
<option value="5">5 - fantastic</option>
</select>
</label>

<label>How interesting is the character? 
<select name="scoreCharacter">
<option value="na"></option>
<option value="1">1 - not at all</option>
<option value="2">2</option>
<option value="3">3</option>
<option value="4">4</option>
<option value="5">5 - fantastic</option>
</select>
</label>

<label>How interesting is the plot? 
<select name="scorePlot">
<option value="na"></option>
<option value="1">1 - not at all</option>
<option value="2">2</option>
<option value="3">3</option>
<option value="4">4</option>
<option value="5">5 - fantastic</option>
</select>
</label>

<label>How believable is the story? 
<select name="scoreBelievable">
<option value="na"></option>
<option value="1">1 - not at all</option>
<option value="2">2</option>
<option value="3">3</option>
<option value="4">4</option>
<option value="5">5 - fantastic</option>
</select>
</label>

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