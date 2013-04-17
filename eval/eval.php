<?php

require_once('parsecsv.lib.php');
$evalResultsFile = "evalResults-test.csv";
$storiesDirectory = "stories";

$scoreFields = array('scoreOverall', "scoreSurprise", "scoreCharacter", "scorePlot", "scoreBelievable");

$itemSubmitted;

// get assignmentId from Amazon
if ($_GET["assignmentId"]) {
  $assignmentId = $_GET["assignmentId"];
} else 
  $assignmentId = "ASSIGNMENT_ID_NOT_AVAILABLE";

// by default, we set it to post to sandbox, unless the request tells us otherwise
$sandbox = true;
if (isset($_REQUEST['destination'])) {
  if ($_REQUEST['destination'] == "production")
    $sandbox = false;
}
  
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

// read the lsit of stories to be evaluated
$fileNames = array();
$dirHandle = opendir($storiesDirectory);
while($storyFName = readdir($dirHandle))
  if ($storyFName != "." && $storyFName != "..")
    array_push($fileNames, $storiesDirectory . "/" . $storyFName);
closedir($dirHandle);

// array with [itemID]['html'] => html representation of the item
// array with [itemID]['N'] => number of evaluations already collected
$itemsToEval = array();

foreach($fileNames as $fname)
  $itemsToEval[$fname]['html'] = file_get_contents($fname);

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
  //echo $itemID . "=>" . $item['N'] . "\n";
  if ($item['N'] < $minN) {
    $minN = $item['N'];
    $minItem = $itemID;
  }
}


?>

<html>
  <head>
    <link rel="stylesheet" href="bootstrap.min.css" type="text/css">
    <script type="text/javascript" src="jquery-1.7.1.js"></script>
    <style>
      body {
      margin: 20px;
      }
    </style>
    <script type="text/javascript">
    
// this function causes data from the form to be first submitted to our server and then to Amazon
    function deliverResults() {
	$.ajax({
	    url: 'eval.php',
            data: {item: $("input[name='item']").val(), scoreSurprise: $("select[name='scoreSurprise']").val(), scoreCharacter: $("select[name='scoreCharacter']").val(), scorePlot: $("select[name='scorePlot']").val(), scoreBelievable: $("select[name='scoreBelievable']").val(), scoreOverall: $("select[name='scoreOverall']").val(), },
            type: 'POST',
            error: function(r,s,t) {},
            success: function(d,s,r){
		// after data are delivered to our server, we submit the form to Amazon
		$('#turkForm').submit();
	    }
    });

    }
    </script>
  </head>

  <body>
    
    <!-- <?php echo "item: " . $fname ?><br/> -->
    
    <h1>Evaluate this story concept</h1>
    <p>Read the story summary below.  It is just a short sketch.
      <!-- It is presented in the form of yes/no questions.-->  Try to imagine what the complete story would look like.
      Tell us how much potential it has.</p>
    
    <div class="well">
      <?php 
	 echo $itemsToEval[$minItem]['html'];
	 ?>
    </div>
    
    <?php
      // here we check whether to post hits to sandbox or to the production version of MTurk
    if ($sandbox)
      echo '<form id="turkForm" action="https://workersandbox.mturk.com/mturk/externalSubmit" method="POST" class="form-horizontal" >';
    else
      echo '<form id="turkForm" action="https://www.mturk.com/mturk/externalSubmit" method="POST" class="form-horizontal" >';	     
       ?> 
    <input type="hidden" name="assignmentId" value="<?php echo $assignmentId; ?>" />

    <form id="evalForm" class="form-horizontal" action="eval.php">
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
   
			   <?php
			   // only include the submit button if the HIT has been accepted
			   if ($assignmentId != "ASSIGNMENT_ID_NOT_AVAILABLE") 
			     echo '<a class="btn btn-primary" onclick="deliverResults(); return false;">Submit</a>';
?>    
    </form>

  </body>
</html>
