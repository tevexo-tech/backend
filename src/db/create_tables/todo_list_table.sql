CREATE TABLE IF NOT EXISTS public.todo_tasks (
    id SERIAL PRIMARY KEY,
    task TEXT NOT NULL,
    due_date DATE,
    task_hash TEXT,
    candidate_id VARCHAR(100) NOT NULL,  -- 👈 added for user-specific tasks
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
