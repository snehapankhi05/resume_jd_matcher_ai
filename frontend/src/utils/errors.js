/**
 * Turn an Axios error into a message that is safe to render.
 *
 * FastAPI returns `detail` as a string for our own errors, but as an
 * ARRAY OF OBJECTS for validation errors (422). Rendering that array in
 * JSX would crash React, so it is always converted to text here.
 */
export function getErrorMessage(error, fallback = "Something went wrong.") {

  const detail = error?.response?.data?.detail;

  if (typeof detail === "string" && detail) {
    return detail;
  }

  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((item) => item?.msg || String(item))
      .join(", ");
  }

  if (error?.code === "ECONNABORTED") {
    return "The request timed out. Please try again.";
  }

  if (error?.request && !error?.response) {
    return "Cannot reach the server. Is the backend running?";
  }

  return fallback;
}
