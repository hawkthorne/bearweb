local utils = {}

function utils.endswith(s, suffix)
  return s:sub(-suffix:len()) == suffix
end

function utils.startswith(s, prefix)
  return s:sub(1, prefix:len()) == prefix
end

return utils
