
import { Card, CardContent, Typography, Grid } from '@mui/material';
import { aggregateAnnotationsByStatus } from "@/lib/actions"
export default async function Stats() {
    const {data: stats} = await aggregateAnnotationsByStatus();

    return (
        <main className="flex min-h-screen flex-col items-center justify-center m-4">
            <div className="flex-grow w-full max-w-5xl">
                <h2 className="text-2xl sm:text-3xl font-extrabold mb-4">Annotation Statistics</h2>
                <Grid container spacing={3}>
                    {Object.keys(stats).map((email) => (
                        <Grid item xs={12} sm={6} md={4} key={email}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" component="div">
                                        {email}
                                    </Typography>
                                    <Typography variant="body1">
                                        <strong>Complete:</strong> {stats[email].complete}
                                    </Typography>
                                    <Typography variant="body1">
                                        <strong>Pending:</strong> {stats[email].pending}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            </div>
        </main>
    );
}
