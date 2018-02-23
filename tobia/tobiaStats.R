

tool_exec = function(inParams, outParams)
{
	message("Start of statiscal analysis for landslides controlled by geological structure")
	
	landslidesPoints = inParams[[1]]
	features = arc.open(landslidesPoints)
	fields = inParams[[2]]
	dataFrameLandslides = arc.select(features, c(fields))
	
	#message(landslidesPoints)
	message(names(dataFrameLandslides))
	
}