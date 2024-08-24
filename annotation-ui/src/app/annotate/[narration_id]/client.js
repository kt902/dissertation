'use client'

import React, { useState } from 'react';
import { Suspense } from 'react';
import Video from '@/components/Video';
import { Container, Typography, Button, FormControl, FormLabel, RadioGroup, FormControlLabel, Radio, Slider, Checkbox, IconButton, Modal, Box } from '@mui/material';
import { Snackbar, Alert, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';

import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from "@hookform/resolvers/yup"
import * as yup from "yup"
import { storeAnnotation } from '@/lib/actions';
// import { useRouter } from 'next/navigation';

const questions = [
    {
        id: 'object_presence',
        label: "How clearly visible are the primary objects involved in the action?",
        options: [
            { value: 1, label: 'Not visible at all' },
            { value: 2, label: 'Barely visible' },
            { value: 3, label: 'Partially visible' },
            { value: 4, label: 'Mostly visible' },
            { value: 5, label: 'Fully visible' }
        ]
    },
    {
        id: 'action_completeness',
        label: "How completely does the video segment capture the entire action, including the beginning and end?",
        options: [
            { value: 1, label: 'Completely misses the action' },
            { value: 2, label: 'Misses significant parts of the action' },
            { value: 3, label: 'Misses some parts of the action' },
            { value: 4, label: 'Nearly complete, minor parts missing' },
            { value: 5, label: 'Completely captures the action' }
        ]
    },
    {
        id: 'focus',
        label: "How well does the video maintain focus on the action, minimizing the impact of distracting objects or movements in the background?",
        options: [
            { value: 1, label: 'Completely unfocused, very distracting' },
            { value: 2, label: 'Often unfocused, many distractions' },
            { value: 3, label: 'Somewhat focused, occasional distractions' },
            { value: 4, label: 'Mostly focused, minimal distractions' },
            { value: 5, label: 'Perfectly focused, no distractions' }
        ]
    },
    {
        id: 'lighting',
        label: "How well does the lighting in the video support clear visibility of the action?",
        options: [
            { value: 1, label: 'Very poorly lit, action barely visible' },
            { value: 2, label: 'Poorly lit, action is difficult to see' },
            { value: 3, label: 'Adequately lit, action is visible but not clear' },
            { value: 4, label: 'Well lit, action is mostly clear' },
            { value: 5, label: 'Perfectly lit, action is very clear' }
        ]
    },
    {
        id: 'camera_motion',
        label: "How well is the camera motion controlled, allowing for clear observation of the action?",
        options: [
            { value: 1, label: 'Very erratic, action is hard to follow' },
            { value: 2, label: 'Somewhat erratic, action is difficult to follow' },
            { value: 3, label: 'Slightly shaky, action is mostly followable' },
            { value: 4, label: 'Mostly smooth, action is easy to follow' },
            { value: 5, label: 'Completely smooth, action is very easy to follow' }
        ]
    }
]

const schema = yup
    .object({
        action_presence: yup.number().integer().required("Please indicate if the action is present in the video."),
        ...questions.reduce((acc, q) => {
            acc[q.id] = yup.number().integer().when('action_presence', {
                is:  1,
                then: () => yup.number().integer().required(`Please rate the ${q.label.toLowerCase()}.`),
                otherwise: () => yup.number().nullable().notRequired()
            });
            return acc;
        }, {})
    })
    .required()

const defaultValues = questions.reduce((acc, q) => {
    acc[q.id] = '';
    return acc;
}, {
    action_presence: ''
});

export default function Annotate({ file, annotation, allCount, completeCount }) {
    const [openSnackbar, setOpenSnackbar] = useState(false);
    const [openDialog, setOpenDialog] = useState(false);
    const [counts, setCounts] = useState({ allCount, completeCount })

    const goToRandomAnnotation = () => {
        window.location.href = '/annotate/random';
    };

    const {
        control,
        handleSubmit,
        formState: { errors },
    } = useForm({
        resolver: yupResolver(schema),
        defaultValues: {
            ...defaultValues,
            ...annotation
        },
    });

    const onSubmit = (data) => {
        setOpenDialog(false);

        storeAnnotation(file.narration_id, data)
            .then(({ allCount, completeCount }) => {
                setCounts({ allCount, completeCount });
                setOpenSnackbar(true);
            })
            .catch(error => {
                console.error("Error saving annotation:", error);
            });
    };

    const handleSaveClick = () => {
        setOpenDialog(true);
    };

    const handleDialogClose = (confirm) => {
        setOpenDialog(false);

        if (confirm) {
            handleSubmit(onSubmit)();
        }
    };

    const [openHelp, setOpenHelp] = useState(false);

    const handleHelpOpen = () => setOpenHelp(true);
    const handleHelpClose = () => setOpenHelp(false);

    return (
        <main className="flex min-h-screen flex-col items-center justify-center m-4 pb-16">
            <div className="flex-grow w-full max-w-5xl space-y-4">
                <h2 className="text-2xl sm:text-3xl font-extrabold">Annotate</h2>

                <Suspense fallback={<div>Loading...</div>}>
                    <>
                        <div className='my-2'>
                            <div className='mr-3 inline'>
                                Completed: {counts.completeCount}/{counts.allCount}
                            </div>
                        </div>
                        <div className='my-2'>
                            <div className='mr-3 inline'>
                                Narration ID: <span className="p-2 bg-red-500 text-white">{file.narration_id}</span>
                            </div>
                            <div className='mr-3 inline'>
                                Action Label: <span className="p-2 bg-red-500 text-white">{file.narration}</span>
                            </div>
                        </div>

                        <Video src={file.url} />

                    </>

                </Suspense>

                <div style={{ flexGrow: 1 }}>
                    <Typography variant="h6" component="h2">
                        Annotation task description
                        <IconButton aria-label="help" onClick={handleHelpOpen} style={{ marginLeft: 8 }}>
                            <HelpOutlineIcon />
                        </IconButton>
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                        Your task is to carefully watch the provided video segment and answer a series of questions that assess the clarity, completeness, and quality of the actions depicted.
                    </Typography>
                </div>

                {/* Annotation Form */}
                <form onSubmit={handleSubmit(onSubmit)} className='flex flex-col w-full items-start justify-start pt-4'>

                    <div className='text-red-400'>
                        {Object.keys(errors).length > 0 && "Please complete all required fields before saving"}
                    </div>

                    {/* Gating Question */}
                    <FormControl component="fieldset" className="mt-4">
                        <FormLabel component="legend">Does this video segment contain the relevant action?</FormLabel>
                        <Controller
                            name="action_presence"
                            control={control}
                            render={({ field }) => (
                                <RadioGroup row {...field}>
                                    <FormControlLabel value="1" control={<Radio />} label="Yes" />
                                    <FormControlLabel value="0" control={<Radio />} label="No" />
                                </RadioGroup>
                            )}
                        />
                    </FormControl>

                    {/* Likert Scale Questions */}
                    {questions.map((q) => (
                        <FormControl component="fieldset" className="mt-4" key={q.id}>
                            <FormLabel component="legend">{q.label}</FormLabel>
                            <Controller
                                name={q.id}
                                control={control}
                                render={({ field }) => (
                                    <RadioGroup {...field}>
                                        {q.options.map(option => (
                                            <FormControlLabel key={option.value} value={option.value} control={<Radio />} label={option.label} />
                                        ))}
                                    </RadioGroup>
                                )}
                            />
                        </FormControl>
                    ))}

                    <div
                        className='flex space-x-4'
                        style={{
                            position: 'fixed',
                            bottom: '20px',
                            right: '20px',
                            zIndex: 1000,
                        }}
                    >
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={handleSaveClick}
                            disabled={Object.keys(errors).length > 0}
                        >
                            Save annotation
                        </Button>
                        <Button
                            variant="contained"
                            color="secondary"
                            onClick={goToRandomAnnotation}
                        >
                            Next
                        </Button>
                    </div>
                </form>
            </div>

            {/* Help Modal */}
            <Modal
                open={openHelp}
                onClose={handleHelpClose}
                aria-labelledby="help-modal-title"
                aria-describedby="help-modal-description"
            >
                <Box sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '80%', bgcolor: 'background.paper', border: '2px solid #000', boxShadow: 24, p: 4 }}>
                    <Typography id="help-modal-title" variant="h6" component="h2">
                        Detailed Help
                    </Typography>
                    <Typography id="help-modal-description" sx={{ mt: 2 }} component="div">
                        <Typography variant="body1" component="p">
                            <strong>Objective:</strong> Your task is to carefully watch the provided video segment and answer a series of questions that assess the clarity, completeness, and quality of the actions depicted.
                        </Typography>

                        <Typography variant="h6" component="h4" gutterBottom sx={{ mt: 2 }}>
                            Instructions:
                        </Typography>
                        <Typography variant="body1" component="ol" sx={{ pl: 2 }}>
                            <li><strong>Focus on the Details:</strong> Pay close attention to the actions performed in the video, the objects involved, and the overall context.</li>
                            <li><strong>Answer Each Question Thoughtfully:</strong> After watching the video, you will be asked a series of questions. These questions are designed to evaluate different aspects of the video, such as how clearly the action is shown, whether all relevant objects are visible, and if the action is complete from start to finish.</li>
                            <li><strong>Provide Honest and Objective Responses:</strong> Your answers should reflect your true observations and interpretations. There are no right or wrong answers, but your input is critical for assessing the quality of the video content.</li>
                            <li><strong>Consider Revisiting the Video:</strong> If necessary, feel free to replay the video to ensure that your answers are accurate and comprehensive.</li>
                        </Typography>

                        <Typography variant="body1" component="p" sx={{ mt: 2 }}>
                            <strong>Goal:</strong> Your responses will help us understand the quality of this video segment, which will contribute to improving the accuracy and effectiveness of our models.
                        </Typography>
                    </Typography>

                    <Button onClick={handleHelpClose} sx={{ mt: 2 }}>Close</Button>
                </Box>
            </Modal>

            {/* Confirmation Dialog */}
            <Dialog
                open={openDialog}
                onClose={() => handleDialogClose(false)}
            >
                <DialogTitle>Confirm Save</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Are you sure you want to save these changes?
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => handleDialogClose(false)} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={() => handleDialogClose(true)} color="primary" autoFocus>
                        Save
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Snackbar */}
            <Snackbar
                open={openSnackbar}
                autoHideDuration={6000}
                onClose={() => setOpenSnackbar(false)}
            >
                <Alert onClose={() => setOpenSnackbar(false)} severity="success" variant="filled">
                    Annotation saved successfully!
                </Alert>
            </Snackbar>

        </main>
    );
}
