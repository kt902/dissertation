// import { useSession, signIn, signOut } from "next-auth/react"

// export default function Component() {
//     const { data: session } = useSession()
//     if (session) {
//         return (
//             <>
//                 Signed in as {session.user.email} <br />
//                 <button onClick={() => signOut()}>Sign out</button>
//             </>
//         )
//     }
//     return (
//         <>
//             Not signed in <br />
//             <button onClick={() => signIn()}>Sign in</button>
//         </>
//     )
// }

import Component from "./component";

import { getServerSession } from "next-auth/next"
import { authOptions } from "@/app/api/auth/[...nextauth]/route"

export default async function Page() {
    const session = await getServerSession(authOptions)


    return <Component session={session}/>
}
