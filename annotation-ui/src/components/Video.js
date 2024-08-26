import React from 'react';


const Video = ({ src }) => {
    return (
        <video
            className="h-full w-full rounded-lg"
            controls={true}
            loop
            muted
            autoPlay
            playsInline
            src={src}
        >
        </video>
    );
};

export default Video;