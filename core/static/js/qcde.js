var player;  // Youtube player object

function resizeHandle(event)
{
    var w = window.innerWidth, h = window.innerHeight;
    var box_el = document.getElementById("videoTopContaier");
    if (w <= 1280)
    {
        player.setSize(1280, 720);
        console.log('resize to 1280');
        box_el.className = box_el.className.replace('h1080', 'h720');

    }
    else
    {
        player.setSize(1920, 1080);
        console.log('resize to 1920');
        box_el.className = box_el.className.replace('h720', 'h1080');
    };
}

function togglePlayback(e)
{
    //console.log("toggle "+player.getPlayerState())
    if (player.getPlayerState() == YT.PlayerState.PLAYING)
    {
        player.pauseVideo();
    }
    else
    {
        player.playVideo();
    };
}

document.getElementById("togglePlay").addEventListener('click', togglePlayback);
window.addEventListener('resize', resizeHandle, true);

function onYouTubeIframeAPIReady()
{
    player = new YT.Player('ytplayer',
    {
        height: '1080',
        width: '1920',
        videoId: video_id,
        playerVars:
        {
            playsinline: 1,
            loop: 1,
            //'enablejsapi': 1,
            autoplay: 1,
            playlist: video_id,
            controls: 0, // Show pause/play buttons in player
            showinfo: 0, // Hide the video title
            fs: 0,
        },
        events:
        {
            'onReady': onPlayerReady,
            'onError' : function(event)
            {
                console.error('player_api', event);
            }
        }
    });
}

// 4. The API will call this function when the video player is ready.
function onPlayerReady(event)
{
    event.target.mute();
    resizeHandle();
    event.target.playVideo();
    console.log("Start playback");
}
