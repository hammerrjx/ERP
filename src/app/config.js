export const field = (key, label, options = {}) => ({ key, label, ...options })
export const columns = (...values) => values.map(([key, label]) => [key, label])
export const config = (title, resource, icon, permission, cols, fields = [], options = {}) => ({
  title, resource, icon, permission, columns: columns(...cols), fields, ...options,
})
export const statusColumn = ['status', '状态']
export const numberColumn = ['number', '单号']
