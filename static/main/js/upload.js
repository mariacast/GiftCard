var upName = '';
var upData = '';
var upOut = '';
var upHash = '';
var upUrl = '';
var upBuf = 131072;
var upTime = 0;
var upAction = '';
var upFin = 0;

function partialUpload(response)
{
    if(typeof upAction == 'function')
        upAction();
    
    if(response != '')
        upOut = response.responseText;
    
    if(upData.length > 0)
    {   
        var fraction = '';
        if(upData.length > upBuf)
        {
            fraction = upData.substring(0, upBuf);
            upData = upData.substring(upBuf);
        }
        else
        {
            fraction = upData;
            upData = '';
        }
            
        ajaxAction
        (
            new Hash(['*action => save', '*upName => '+upName, '*upData => '+fraction, '*upOut => '+upOut]),
            upUrl,
            partialUpload
        );
    }
    else
    {
        ajaxAction
        (
            new Hash(['*action => hash', '*upName => '+upOut]),
            upUrl,
            partialOk
        );
    }
}

function partialOk(response)
{
    upHash = response.responseText;
    
    var sec = new Date().getTime();
    sec = sec - upTime;
    sec = sec / 1000;
    upTime = sec;
    upFin = 1;
    
    if(typeof upAction == 'function')
        upAction();
}

function partialClear()
{
    upName = '';
    upData = '';
    upOut = '';
    upHash = '';
    upTime = 0;
    upFin = 0;
}
