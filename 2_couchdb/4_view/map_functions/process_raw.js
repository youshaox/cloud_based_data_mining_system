//group 25
//* Youshao Xiao - 876548
//* Jiaheng Zhu - 848432
//* Lina Zhou - 941539
//* Haimei Liu - 895804
//* Miaomiao Zhang - 895216

// Map function to get helpful data from raw data


function(doc){
    emit(doc.id,{"coordinates":doc.place.bounding_box.coordinates,"coordinates2":doc.coordinates,"location":doc.user.location,"source":doc.source,"text":doc.text});
}
