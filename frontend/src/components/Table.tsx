import React from 'react';

interface Column<T> {
  key: keyof T | string;
  title: string;
  render?: (value: any, record: T, index: number) => React.ReactNode;
  className?: string;
  width?: string;
  align?: 'left' | 'center' | 'right';
}

interface TableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey: keyof T | ((record: T, index: number) => string);
  loading?: boolean;
  empty?: React.ReactNode;
  onRowClick?: (record: T, index: number) => void;
  striped?: boolean;
  hover?: boolean;
  className?: string;
}

export const Table = React.forwardRef<HTMLTableElement, TableProps<any>>(
  (
    {
      columns,
      data,
      rowKey,
      loading = false,
      empty = 'No data available',
      onRowClick,
      striped = true,
      hover = true,
      className = '',
    },
    ref
  ) => {
    const getRowKey = (record: any, index: number) => {
      if (typeof rowKey === 'function') {
        return rowKey(record, index);
      }
      return record[rowKey] ?? index;
    };

    const getAlignClass = (align?: string) => {
      switch (align) {
        case 'center':
          return 'text-center';
        case 'right':
          return 'text-right';
        default:
          return 'text-left';
      }
    };

    return (
      <div className={`overflow-x-auto ${className}`}>
        <table ref={ref} className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100 border-b border-gray-300">
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  className={`px-6 py-3 font-semibold text-gray-900 ${getAlignClass(
                    column.align
                  )} ${column.className || ''}`}
                  style={{ width: column.width }}
                >
                  {column.title}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-8 text-center">
                  <div className="flex justify-center items-center">
                    <div className="animate-spin h-6 w-6 border-b-2 border-blue-600 rounded-full"></div>
                    <span className="ml-2 text-gray-600">Loading...</span>
                  </div>
                </td>
              </tr>
            ) : data.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-6 py-8 text-center text-gray-500">
                  {empty}
                </td>
              </tr>
            ) : (
              data.map((record, index) => (
                <tr
                  key={getRowKey(record, index)}
                  className={`border-b border-gray-200 ${
                    striped && index % 2 === 1 ? 'bg-gray-50' : ''
                  } ${
                    hover ? 'hover:bg-blue-50 cursor-pointer transition-colors' : ''
                  }`}
                  onClick={() => onRowClick && onRowClick(record, index)}
                >
                  {columns.map((column) => (
                    <td
                      key={String(column.key)}
                      className={`px-6 py-4 text-gray-900 ${getAlignClass(column.align)} ${
                        column.className || ''
                      }`}
                    >
                      {column.render
                        ? column.render((record as any)[String(column.key)], record, index)
                        : (record as any)[String(column.key)]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    );
  }
);

Table.displayName = 'Table';
