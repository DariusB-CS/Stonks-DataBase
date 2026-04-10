import { createClient } from "@supabase/supabase-js"

const supaURL = "https://sdljiupgexkfclwkfcnt.supabase.co";
const supaKey = "sb_publishable_zYbO2hiwUP4XXNDfmHN2uw_JjvL_xCc";

export const supabase = createClient(supaURL, supaKey);