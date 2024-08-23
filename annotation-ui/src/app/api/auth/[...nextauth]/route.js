import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials";
import client from "@/lib/mongodb";
import { cookies } from 'next/headers'

export const authOptions = {
    pages: {
        // signIn: "/login",
    },
    providers: [
        CredentialsProvider({
            // The name to display on the sign in form (e.g. "Sign in with...")
            name: "Credentials",
            // `credentials` is used to generate a form on the sign in page.
            // You can specify which fields should be submitted, by adding keys to the `credentials` object.
            // e.g. domain, username, password, 2FA token, etc.
            // You can pass any HTML attribute to the <input> tag through the object.
            credentials: {
                username: { label: "Username", type: "text", placeholder: "user@bath.ac.uk" },
                password: { label: "Password", type: "password" }
            },
            async authorize(credentials, req) {
                const mongoClient = await client.connect();
                try {
                    const database = mongoClient.db(process.env.DB_NAME); // Replace with your actual database name
                    const usersCollection = database.collection("users"); // Replace with your actual collection name
            
                    // Look up the user by the email (username)
                    const user = await usersCollection.findOne({ email: credentials.username });
            
                    if (user) {
                        // Check if the password matches
                        const passwordMatches = user.password === credentials.password; // In production, you should hash passwords
            
                        if (passwordMatches) {
                            // Return user details if the email and password match
                            cookies().set('current_dataset', '');

                            return { id: user._id, email: user.email };
                        }
                    }
            
                    // If no user is found or password doesn't match, return null
                    return null;
            
                } catch (error) {
                    console.error("Authorization error:", error);
                    return null; // You can handle the error in a better way as per your requirements
                } finally {
                    await mongoClient.close(); // Close the connection
                }
            }            
        })
    ]
}

async function handler(req, res) {
    // Do whatever you want here, before the request is passed down to `NextAuth`
    return await NextAuth(req, res, authOptions)
}

export { handler as GET, handler as POST }