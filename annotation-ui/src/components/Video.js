import React from 'react';


const Video = ({ src }) => {
    return (
        <video
            className="h-full w-full rounded-lg"
            controls={true}
            loop
            autoPlay
            src={src}
        />
    );
};

export default Video;