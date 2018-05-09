// Map function to get helpful data from raw data


function(doc){
    emit(doc.id,{"coordinates":doc.place.bounding_box.coordinates,"coordinates2":doc.coordinates,"location":doc.user.location,"source":doc.source,"text":doc.text});
}