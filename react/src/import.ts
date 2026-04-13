import { supabase } from './supabaseClient';

/**
 * Tracks a stock for the currently logged-in user.
 * @param stockName The name of the stock to find in the 'stocks' table.
 */
async function trackStock(stockName: string) {
  try {
    // 1. Get the current authenticated User's ID
    // Your RLS policies rely on auth.uid(), so this is the safest way to get the ID.
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    
    if (authError || !user) {
      throw new Error("User must be authenticated to track stocks.");
    }
    const userId = user.id;

    // 2. Get the Stock ID from the 'stocks' table
    const { data: stockData, error: stockError } = await supabase
      .from('stocks')
      .select('id, Price')
      .eq('name', stockName)
      .single(); // Use .single() because we expect one specific stock

    if (stockError || !stockData) {
      throw new Error(`Stock '${stockName}' not found.`);
    }
    const stockId = stockData.id;
    const currentPrice = stockData.Price;

    // 3. Insert into 'tracked_stocks'
    // The 'id' and 'created_at' are generated automatically by the database.
    const { data: newTrackedStock, error: insertError } = await supabase
      .from('tracked_stocks')
      .insert([
        { 
          user_id: userId, 
          stock_id: stockId,
          Price: currentPrice, // Capturing the price at the moment of tracking
          History: {} // Initializing History as an empty JSON object
        }
      ])
      .select() // This returns the newly created row, including the generated 'id'
      .single();

    if (insertError) throw insertError;

    console.log('Successfully created tracked stock with ID:', newTrackedStock.id);
    return newTrackedStock;

  } catch (error) {
    console.error('Operation failed:', error.message);
    return null;
  }
}
