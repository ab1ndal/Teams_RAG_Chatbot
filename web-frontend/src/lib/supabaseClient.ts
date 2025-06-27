// Supabase client
// web-frontend/src/lib/supabaseClient.ts

import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function createClient() {
    const cookieStore = await cookies();
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

    return createServerClient(supabaseUrl, supabaseAnonKey, {
        cookies: {
            getAll(){
                return cookieStore.getAll();
            },
            setAll(cookiesToSet){
                try{
                    cookiesToSet.forEach(cookie => cookieStore.set(cookie.name, cookie.value, cookie.options));
                }
                catch{
                    //No Errors caught
                }
            }
        }
    });
}
