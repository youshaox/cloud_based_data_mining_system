// Map function to find the position of tweet and the sentiment value of each one
// _sum will be used as a  reduce function
// group_level = 1 for the accumulated value of each state
// group_level = 2 for the accumulated value of each district in Victoria
// group_level = 3 for the accumulated value of each district in Melbourne


function(doc) {

  emit([doc.state,doc.districtInVic,doc.districInMel], doc.sentiment);


}