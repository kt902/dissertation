"use server";

import client from "@/lib/mongodb";

export async function testDatabaseConnection() {
    let isConnected = false;
    try {
        const mongoClient = await client.connect();
        // Send a ping to confirm a successful connection
        await mongoClient.db("admin").command({ ping: 1 });
        console.log(
            "Pinged your deployment. You successfully connected to MongoDB!",
        ); // because this is a server action, the console.log will be outputted to your terminal not in the browser
        return !isConnected;
    } catch (e) {
        console.error(e);
        return isConnected;
    }
}

// import { ObjectId } from 'mongodb'; // If you're using MongoDB's ObjectId

import { authOptions } from "@/app/api/auth/[...nextauth]/route";
import { getServerSession } from "next-auth/next";

export async function getAnnotationByNarrationId(narrationId) {
    try {
        const session = await getServerSession(authOptions);
        const userId = session.user.email;

        const mongoClient = await client.connect();
        const database = mongoClient.db(process.env.DB_NAME); // Replace with your actual database name
        const collection = database.collection("annotation_queue"); // Replace with your actual collection name


        // Find the annotation by narrationId
        const annotation = await collection.findOne({ user_id: userId, narration_id: narrationId });

        // Count complete annotations
        const completeCount = await collection.countDocuments({ user_id: userId, status: "complete" });

        // Count all annotations
        const allCount = await collection.countDocuments({ user_id: userId });


        if (!annotation) {
            return {
                success: false,
                message: "No annotation found for the provided narration ID",
            };
        }

        return {
            success: true,
            annotation: {
                ...annotation,
                _id: annotation._id.toString()
            },
            completeCount,
            allCount
        };
    } catch (e) {
        console.error("Error retrieving annotation:", e);
        return {
            success: false,
            message: "Failed to retrieve annotation",
            error: e.message,
        };
    }
}

export async function getAnnotations() {
    try {
        const session = await getServerSession(authOptions);
        const userId = session.user.email;

        const mongoClient = await client.connect();
        const database = mongoClient.db(process.env.DB_NAME); // Replace with your actual database name
        const collection = database.collection("annotation_queue"); // Replace with your actual collection name

        // Find all annotations for the given user_id and project only the status and narration_id fields
        const annotations = await collection.find(
            { user_id: userId }, // Query filter to match the user_id
            { projection: { _id: 0, status: 1, narration_id: 1 } } // Projection to include only status and narration_id, exclude _id
        ).toArray();

        return {
            success: true,
            data: annotations,
        };
    } catch (e) {
        console.error("Error retrieving annotations:", e);
        return {
            success: false,
            message: "Failed to retrieve annotations",
            error: e.message,
        };
    }
}


export async function storeAnnotation(narrationId, annotationData) {
    try {
        const session = await getServerSession(authOptions);
        const userId = session.user.email;

        const mongoClient = await client.connect();
        const database = mongoClient.db(process.env.DB_NAME); // Replace with your actual database name
        const collection = database.collection("annotation_queue"); // Replace with your actual collection name

        // Perform an upsert operation (update if exists, insert if not)
        const result = await collection.updateOne(
            { user_id: userId, narration_id: narrationId }, // Filter by narrationId
            {
                $set: {
                    annotation: annotationData,
                    status: 'complete'
                }, // Update the document with the new annotation data
            },
        );

        // Count pending annotations
        const completeCount = await collection.countDocuments({ user_id: userId, status: "complete" });

        // Count all annotations
        const allCount = await collection.countDocuments({ user_id: userId });


        return {
            success: true,
            upsertedId: String(result.upsertedId), // Return the upsertedId or the existing narrationId
            completeCount,
            allCount
        };
    } catch (e) {
        return {
            success: false,
            message: "Failed to store annotation",
            error: e.message,
        };
    }
}

export async function getRandomPendingAnnotation() {
    try {
        const session = await getServerSession(authOptions);
        const userId = session.user.email;

        const mongoClient = await client.connect();
        const database = mongoClient.db(process.env.DB_NAME);
        const collection = database.collection("annotation_queue");

        // Count the total number of pending annotations
        const pendingCount = await collection.countDocuments({ user_id: userId, status: "pending" });
        if (pendingCount === 0) {
            return {
                success: false,
                message: "No pending annotations available",
            };
        }

        // Generate a random skip value
        const randomSkip = Math.floor(Math.random() * pendingCount);

        // Find one random pending annotation
        const annotation = await collection.findOne({ user_id: userId, status: "pending" }, { skip: randomSkip });

        if (!annotation) {
            return {
                success: false,
                message: "Failed to retrieve a random pending annotation",
            };
        }

        return {
            success: true,
            annotation: {
                ...annotation,
                _id: annotation._id.toString(),
            },
        };
    } catch (e) {
        console.error("Error retrieving random pending annotation:", e);
        return {
            success: false,
            message: "Failed to retrieve random pending annotation",
            error: e.message,
        };
    }
}


export async function aggregateAnnotationsByStatus() {
    try {
        const mongoClient = await client.connect();
        const database = mongoClient.db(process.env.DB_NAME); // Replace with your actual database name
        const collection = database.collection("annotation_queue"); // Replace with your actual collection name

        const aggregationResult = await collection.aggregate([
            {
                $group: {
                    _id: { user_id: "$user_id", status: "$status" }, // Group by user_id and status
                    count: { $sum: 1 } // Count the number of annotations for each group
                }
            },
            {
                $group: {
                    _id: "$_id.user_id", // Group by user_id to structure the results by user
                    statuses: {
                        $push: {
                            k: "$_id.status",
                            v: "$count"
                        }
                    }
                }
            },
            {
                $addFields: {
                    statuses: {
                        $mergeObjects: [
                            { complete: 0, pending: 0, in_progress: 0, review: 0 }, // All possible statuses with default values
                            { $arrayToObject: "$statuses" } // Convert the statuses array to an object
                        ]
                    }
                }
            },
            {
                $project: {
                    _id: 0, // Exclude the default _id field
                    user_id: "$_id", // Rename _id to user_id for clarity
                    statuses: 1 // Keep the statuses field
                }
            }
        ]).toArray();

        // Convert the array of results to the desired object format
        const resultAsObject = aggregationResult.reduce((acc, item) => {
            acc[item.user_id] = item.statuses;
            return acc;
        }, {});

        return {
            success: true,
            data: resultAsObject,
        };
    } catch (e) {
        console.error("Error aggregating annotations by status:", e);
        return {
            success: false,
            message: "Failed to aggregate annotations by status",
            error: e.message,
        };
    }
}

