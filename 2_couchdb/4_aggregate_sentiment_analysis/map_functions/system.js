//Map function to find the the distribution of phone system on each state
// _count as reduce function
//group_level = 2 for the number of each system on each state


function(doc) {
  if(doc.system !== null){
    emit([doc.state,doc.system], 1);
  }
}